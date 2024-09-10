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

export const links = [] satisfies NavItem[]

export type ActivePaths = (typeof links)[number]['href']
const defaultLink = (props: ComponentProps<'a'>) => <a {...props}></a>
export type Link = typeof NextLink | typeof defaultLink
