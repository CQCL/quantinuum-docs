import { ComponentProps } from 'react'


export const textLinks = navTextLinks;
export const productName = navProductName;

export type ActivePaths = (typeof textLinks)[number]['href']
const defaultLink = (props: ComponentProps<'a'>) => <a {...props}></a>
export type Link = typeof defaultLink
