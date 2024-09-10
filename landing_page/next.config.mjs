import { z } from 'zod'

export const runtimeENVs = z.object({
  BASE_PATH: z.string()
})

const values = runtimeENVs.parse(process.env)
export default { 
  output: 'export',
  images: { unoptimized: true },
  assetPrefix: values.BASE_PATH + "/",
  basePath: values.BASE_PATH
}
