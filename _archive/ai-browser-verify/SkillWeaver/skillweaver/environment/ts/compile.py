import os

# Must have tsc installed (or just use the existing .js files).
# First create a combined file, removing any import statements.
# Then compile the combined file.
prev_dir = os.getcwd()
os.chdir(os.path.dirname(__file__))

with open("domUtils.ts", "r") as f:
    domUtils = f.read()

with open("roleUtils.ts", "r") as f:
    roleUtils = f.read()

with open("_compiled_0.ts", "w") as f:
    f.write(domUtils)
    f.write(
        "\n".join(
            line
            for line in roleUtils.split("\n")
            if not (line.startswith("import") and "domUtils" in line)
        )
    )

# downlevelIteration: required for certain Typescript features
# commonjs: so it's easy for us to inject the script
# target: so NodeListOf is considered an iterable
os.system("tsc --downLevelIteration --module commonjs --target es6 _compiled_0.ts")

# prepend _compiled.ts with the string "const exports = {}"
os.system('echo "const exports = {}" > _compiled.js')
os.system("cat _compiled_0.js >> _compiled.js")
os.system("rm _compiled_0.js _compiled_0.ts")

os.chdir(prev_dir)
