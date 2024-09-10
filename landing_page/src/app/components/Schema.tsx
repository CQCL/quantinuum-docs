import { z } from 'zod'

const ProductLinks = z.object({
    title: z.string(),
    description: z.string(),
    url: z.string()
})


export const ProductSchema = z.array(z.object({
    logo: z.string(),
    logo_link: z.string(),
    // logo_desription: z.string(),
    description: z.string(),
    links: z.array(ProductLinks)
}))
