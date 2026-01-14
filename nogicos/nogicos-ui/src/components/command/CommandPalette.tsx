"use client"

import * as React from "react"
import { useEffect, useState, useCallback } from "react"
import { Settings, Sparkles, Trash2, Moon, Plus } from "lucide-react"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command"

interface CommandPaletteProps {
  onNewSession?: () => void
  onClearHistory?: () => void
  onToggleTheme?: () => void
}

type CommandAction = {
  id: string
  label: string
  icon: React.ReactNode
  shortcut?: string
  action: () => void
  group: string
}

export function CommandPalette({
  onNewSession,
  onClearHistory,
  onToggleTheme,
}: CommandPaletteProps) {
  const [open, setOpen] = useState(false)

  // KeyboardHotkey: Cmd/Ctrl+K
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((prev) => !prev)
      }
    }

    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  // Electron IPC Listen
  useEffect(() => {
    const api = (window as Window & { electronAPI?: { onToggleCommandPalette?: (cb: () => void) => () => void } }).electronAPI
    if (api?.onToggleCommandPalette) {
      const cleanup = api.onToggleCommandPalette(() => {
        setOpen((prev) => !prev)
      })
      return cleanup
    }
  }, [])

  const runCommand = useCallback((command: () => void) => {
    setOpen(false)
    command()
  }, [])

  const commands: CommandAction[] = [
    // Session
    {
      id: "new-session",
      label: "New Session",
      icon: <Plus className="mr-2 h-4 w-4" />,
      shortcut: "⌘N",
      action: () => onNewSession?.(),
      group: "Session",
    },
    {
      id: "clear-history",
      label: "Clear Chat History",
      icon: <Trash2 className="mr-2 h-4 w-4" />,
      action: () => onClearHistory?.(),
      group: "Session",
    },
    // Quick Actions
    {
      id: "quick-ask",
      label: "Quick Ask AI",
      icon: <Sparkles className="mr-2 h-4 w-4" />,
      shortcut: "⌘⏎",
      action: () => {
        // Focus on input
        const input = document.querySelector('textarea[placeholder*="Message"]') as HTMLTextAreaElement
        input?.focus()
      },
      group: "Actions",
    },
    // Settings
    {
      id: "toggle-theme",
      label: "Toggle Dark/Light Mode",
      icon: <Moon className="mr-2 h-4 w-4" />,
      shortcut: "⌘D",
      action: () => onToggleTheme?.(),
      group: "Settings",
    },
    {
      id: "settings",
      label: "Open Settings",
      icon: <Settings className="mr-2 h-4 w-4" />,
      shortcut: "⌘,",
      action: () => {
        // TODO: Open settings dialog
      },
      group: "Settings",
    },
  ]

  // Group commands
  const groupedCommands = commands.reduce((acc, cmd) => {
    if (!acc[cmd.group]) acc[cmd.group] = []
    acc[cmd.group].push(cmd)
    return acc
  }, {} as Record<string, CommandAction[]>)

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <div className="flex flex-col">
        {/* Custom styled input */}
        <CommandInput 
          placeholder="Type a command or search..." 
          className="border-none focus:ring-0"
        />
        <CommandList className="max-h-[400px]">
          <CommandEmpty>No results found.</CommandEmpty>
          
          {Object.entries(groupedCommands).map(([group, items], groupIndex) => (
            <React.Fragment key={group}>
              {groupIndex > 0 && <CommandSeparator />}
              <CommandGroup heading={group}>
                {items.map((item) => (
                  <CommandItem
                    key={item.id}
                    onSelect={() => runCommand(item.action)}
                    className="cursor-pointer"
                  >
                    {item.icon}
                    <span>{item.label}</span>
                    {item.shortcut && (
                      <CommandShortcut>{item.shortcut}</CommandShortcut>
                    )}
                  </CommandItem>
                ))}
              </CommandGroup>
            </React.Fragment>
          ))}
        </CommandList>
        
        {/* Footer hint */}
        <div className="flex items-center justify-between border-t border-white/5 px-3 py-2 text-xs text-white/40">
          <div className="flex items-center gap-2">
            <kbd className="rounded bg-white/10 px-1.5 py-0.5">↑↓</kbd>
            <span>Navigate</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="rounded bg-white/10 px-1.5 py-0.5">↵</kbd>
            <span>Select</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="rounded bg-white/10 px-1.5 py-0.5">esc</kbd>
            <span>Close</span>
          </div>
        </div>
      </div>
    </CommandDialog>
  )
}

export default CommandPalette

