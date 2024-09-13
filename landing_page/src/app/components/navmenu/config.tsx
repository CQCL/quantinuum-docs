import NextLink from 'next/link'
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
    title: 'H-Series',
    href: 'https://docs.quantinuum.com/h-series',
    pathMatch: '/h-series',
  },
  {
    title: 'Nexus',
    href: 'https://docs.quantinuum.com/nexus',
    pathMatch: '/nexus',
  },
  {
    title: 'TKET',
    href: 'https://docs.quantinuum.com/tket',
    pathMatch: '/tket',
  },
  {
    title: 'InQuanto',
    href: 'https://docs.quantinuum.com/inquanto',
    pathMatch: '/inquanto',
  },
  {
    title: 'lambeq',
    href: 'https://docs.quantinuum.com/lambeq',
    pathMatch: '/lambeq',
  },
] satisfies NavItem[]

export type ActivePaths = (typeof links)[number]['href']
const defaultLink = (props: ComponentProps<'a'>) => <a {...props}></a>
export type Link = typeof NextLink | typeof defaultLink
