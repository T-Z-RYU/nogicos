import asyncio
import json
import os
import random
import socket
import threading
import time
from typing import Optional

import docker
import docker.models.containers
import requests

WIKIPEDIA_DATA_FOLDER = os.path.dirname(__file__) + "/../../../wikipedia_data"
HOSTNAME = os.getenv("IP", "127.0.0.1")
ORCHESTRATION_SERVER_ADDRESS = (
    os.getenv("IP", "127.0.0.1") + ":" + os.getenv("ORCHESTRATION_SERVER_PORT", "5125")
)

with open(os.path.join(os.path.dirname(__file__), "containers.json")) as f:
    container_specs = json.load(f)


def shopping_init(container, hostname: str, external_port: int):
    print(
        "Initializing shopping container with hostname",
        hostname,
        "and external port",
        external_port,
    )
    time.sleep(5.0)
    container.exec_run(
        f"/var/www/magento2/bin/magento setup:store-config:set --base-url=http://{hostname}:{external_port}"
    )
    container.exec_run(
        f'mysql -u magentouser -pMyPassword magentodb -e \'UPDATE core_config_data SET value="http://{hostname}:{external_port}/" WHERE path = "web/secure/base_url";\''
    )
    container.exec_run("/var/www/magento2/bin/magento cache:flush")
    time.sleep(5.0)


def shopping_admin_init(container, hostname: str, external_port: int):
    print(
        "Initializing shopping admin container with hostname",
        hostname,
        "and external port",
        external_port,
    )
    shopping_init(container, hostname, external_port)


def gitlab_init(container, hostname: str, external_port: int):
    print(
        "Initializing gitlab container with hostname",
        hostname,
        "and external port",
        external_port,
    )
    container.exec_run(
        f"sed -i \"s|^external_url.*|external_url 'http://{hostname}:{external_port}'|\" /etc/gitlab/gitlab.rb"
    )
    container.exec_run("gitlab-ctl reconfigure")
    container.exec_run("gitlab-ctl restart")
    time.sleep(35.0)
    # needed sometimes to close old connections
    container.exec_run("gitlab-ctl restart postgresql")
    time.sleep(10.0)  # allow server to start up


def reddit_init(container, hostname: str, external_port: int):
    print("Waiting 30 seconds for server to start up.")
    time.sleep(30.0)  # allow server to start up

def get_docker_client():
    if os.path.exists("/var/run/docker.sock"):
        client = docker.from_env()
    else:
        client = docker.DockerClient(
            base_url=f"unix://{os.getenv('XDG_RUNTIME_DIR')}/docker.sock"
        )

    return client


# Used on server-side.
class Orchestrator:
    def __init__(
        self,
        pool_size: int = 3,
        start_port: int = 8000,
        container_hostname: str = "127.0.0.1",
    ):
        self.pool_size = pool_size
        self.start_port = start_port
        self.end_port = start_port + 1000
        self.next_port = start_port
        self.active = set()
        self.client = get_docker_client()
        self.container_hostname = container_hostname
        self.port_lock = threading.Lock()
        self.ports = set()
        self.used_ports = {}

    def obtain_container(
        self, name: str
    ) -> tuple[docker.models.containers.Container, int]:
        container, port = self._start_docker(name)
        self.active.add(container.name)
        self.used_ports[container.id] = port
        return container, port

    def release_container(self, id: str):
        container = self.client.containers.get(id)
        container.stop()
        self.active.remove(container.name)
        self.ports.remove(self.used_ports[container.id])
        del self.used_ports[container.id]

    def _is_port_available(self, port: int):
        if port in self.used_ports.values():
            return False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
            return True
        except OSError:
            return False

    def _obtain_port(self) -> int:
        with self.port_lock:
            initial_port = self.next_port
            port = initial_port
            while not self._is_port_available(port):
                port += 1
                if port >= self.end_port:
                    port = self.start_port
                elif port == initial_port:
                    raise Exception("No available ports")
            self.next_port = port + 1
            self.ports.add(port)
        return port

    def _start_docker(
        self, name: str
    ) -> tuple[docker.models.containers.Container, int]:
        spec = container_specs[name]
        internal_port = spec["internal_port"]
        image_name = spec["image_name"]

        volumes = {}
        if name == "wikipedia":
            volumes = {WIKIPEDIA_DATA_FOLDER: {"bind": "/data", "mode": "ro"}}
        environment = {}
        entrypoint_args = spec.get("entrypoint_args", [])

        for attempt in range(5):
            try:
                external_port = self._obtain_port()
                if name == "gitlab":
                    internal_port = external_port
                container = self.client.containers.run(
                    image_name,
                    name=f"{name}_{external_port}",
                    detach=True,
                    ports={str(internal_port): external_port},
                    volumes=volumes,
                    environment=environment,
                    command=entrypoint_args,
                    remove=True,
                    shm_size="256m" if name == "gitlab" else None,
                )
                break
            except Exception as e:
                import traceback

                print("!!! Exception:", e)
                traceback.print_exc()
                if "is already in use" not in str(e):
                    raise

                if attempt == 4:
                    raise

                time.sleep(random.random() * 5.0)
        self._init_docker(name, container, external_port)

        return container, external_port

    def _init_docker(
        self, name: str, container: docker.models.containers.Container, port: int
    ):
        init_fn_name = container_specs[name].get("init")
        if init_fn_name is None:
            return

        init_fn = globals()[init_fn_name]
        init_fn(container, self.container_hostname, int(port))


MAP_SPECIAL_STRING = "<<MAP>>"
CLASSIFIEDS_SPECIAL_STRING = "<<CLASSIFIEDS>>"


async def _fake_map_coroutine():
    return MAP_SPECIAL_STRING


async def _fake_classifieds_coroutine():
    return CLASSIFIEDS_SPECIAL_STRING


# Context manager for containerization.
# Used on client side.
class containers:
    """
    This is a context manager. Use it like this:

    ```
    with containers(["shopping", "gitlab"]) as container_addresses:
        ...
    ```

    Where container_addresses provides you with a dictionary mapping site names (e.g. 'shopping') to their hostnames (e.g. ip:port).
    """

    def __init__(self, sites: list[str]):
        self.sites = sites
        self.container_params = {}

    async def __aenter__(self) -> dict[str, str]:
        loop = asyncio.get_running_loop()
        responses = await asyncio.gather(
            *[
                (
                    loop.run_in_executor(
                        None,
                        requests.get,
                        f"http://{ORCHESTRATION_SERVER_ADDRESS}/obtain/{site.split(':')[0]}",  # allow "shopping:1", etc. for parallel cases
                    )
                    if site.split(":")[0] not in ["map", "classifieds"]
                    else (
                        _fake_map_coroutine()
                        if site.split(":")[0] == "map"
                        else _fake_classifieds_coroutine()
                    )
                )
                for site in self.sites
            ]  # type: ignore
        )

        cancel_exception: Optional[Exception] = None

        container_params = {}
        container_addresses = {}
        for site, response in zip(self.sites, responses):
            if response == MAP_SPECIAL_STRING:
                container_params[site] = MAP_SPECIAL_STRING
                map_addr = os.getenv("MAP_ADDR")
                assert (
                    map_addr is not None
                ), "Must supply an address for Maps in MAP_ADDR"
                if map_addr.startswith("http://"):
                    map_addr = map_addr[7:]
                container_addresses[site] = map_addr
                continue
            elif response == CLASSIFIEDS_SPECIAL_STRING:
                container_params[site] = CLASSIFIEDS_SPECIAL_STRING
                classifieds_addr = os.getenv("CLASSIFIEDS")
                assert (
                    classifieds_addr is not None
                ), "Must supply an address for Classifieds in CLASSIFIEDS"
                if classifieds_addr.startswith("http://"):
                    classifieds_addr = classifieds_addr[7:]
                container_addresses[site] = classifieds_addr
                continue

            if response is None or response.status_code != 200:
                cancel_exception = Exception(
                    f"Failed to obtain container for site {site}: {response.text if response else '<no response>'}"
                )
                # Don't raise yet because we want to know if any other containers were successfully obtained.
                # (So we can release them immediately)
            else:
                container_params[site] = (
                    response.json()
                )  # contains 'host', 'port', 'id'
                container_addresses[site] = (
                    container_params[site]["host"]
                    + ":"
                    + str(container_params[site]["port"])
                )

        if cancel_exception is not None:
            await self._release(container_params)

            raise cancel_exception

        self.container_params = container_params

        return container_addresses

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._release(self.container_params)

    async def _release(self, container_params):
        loop = asyncio.get_running_loop()
        await asyncio.gather(
            *[
                loop.run_in_executor(
                    None,
                    requests.get,
                    f"http://{ORCHESTRATION_SERVER_ADDRESS}/release/{container['id']}",
                )
                for container in container_params.values()
                if container != MAP_SPECIAL_STRING
                and container != CLASSIFIEDS_SPECIAL_STRING
            ]
        )
