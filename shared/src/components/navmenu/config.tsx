import { ComponentProps } from 'react'

type NavItem = {
  title: string
  href: string
  target?: string
  pathMatch: string
  megamenu?: {
    title: string
    href: string
    description: string
  }[]
}

export const links = [
  {
    title: 'API Docs',
    href: 'api-docs',
    pathMatch: '/api-docs',
  },
  {
    title: 'Examples',
    href: 'examples',
    pathMatch: '/examples',
  },
  {
    title: 'Blog',
    href: 'blog/',
    pathMatch: '/blog',
  },
  {
    title: 'User Manual',
    href: 'user-manual',
    pathMatch: '/user-manual',
  },
] satisfies NavItem[]

export type ActivePaths = (typeof links)[number]['href']
const defaultLink = (props: ComponentProps<'a'>) => <a {...props}></a>
export type Link = typeof defaultLink
