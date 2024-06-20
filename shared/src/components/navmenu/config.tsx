import { ComponentProps } from 'react'
import { z } from 'zod';


const linkSchema = z.object({
    href: z.string(),
    title: z.string(),
    pathMatch: z.string(),
    external: z.boolean().optional().default(false),
});
export const navConfigSchema = z.object({
    navTextLinks: z.array(linkSchema),
    navIconLinks: z.array(z.intersection(linkSchema, z.object({iconImageURL: z.string()}))),
    navProductName: z.string()

})

export const navConfig = navConfigSchema.parse({
    navTextLinks: typeof navTextLinks !== "undefined" ? navTextLinks : null,
    navIconLinks: typeof navIconLinks !== "undefined" ? navIconLinks : null,
    navProductName: typeof navProductName !== "undefined" ? navProductName : null
})

export type ActivePaths = (typeof navConfig['navTextLinks'])[number]['href']
const defaultLink = (props: ComponentProps<'a'>) => <a {...props}></a>
export type Link = typeof defaultLink
