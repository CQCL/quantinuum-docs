
import React from 'react'
import { Check, MoonIcon, SunIcon } from 'lucide-react'
import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  Skeleton,
  useTheme,
  //@ts-ignore
} from '@cqcl/quantinuum-ui'

export const ModeSelector = () => {
  const [isMounted, setIsMounted] = React.useState(false)
  const theme = useTheme()
  React.useEffect(() => {
    setIsMounted(true)
  }, [])
  if (!isMounted)
    return <Skeleton className="bg-muted h-6 w-6 rounded"></Skeleton>
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className="aspect-square w-9 px-0"
          aria-label="theme-selector"
        >
          <SunIcon className="h-[1.15rem] w-[1.15rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <MoonIcon className="absolute h-[1.15rem] w-[1.15rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <div className="text-muted-foreground mb-1 ml-2 mt-1  text-xs">
          Select Theme
        </div>
        <DropdownMenuItem onClick={() => theme.setMode('light')}>
          Light
          {theme.theme.mode === 'light' ? (
            <Check className="ml-auto aspect-square w-4"></Check>
          ) : null}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => theme.setMode('dark')}>
          Dark
          {theme.theme.mode === 'dark' ? (
            <Check className="ml-auto aspect-square w-4"></Check>
          ) : null}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => theme.setMode('system')}>
          System
          {theme.theme.mode === 'system' ? (
            <Check className="ml-auto aspect-square w-4"></Check>
          ) : null}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
