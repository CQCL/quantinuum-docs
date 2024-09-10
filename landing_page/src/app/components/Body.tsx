import { Card, Logo } from './Card'
import text from './text.json'
import { ProductSchema } from './Schema'
import Image from 'next/image'
import Link from 'next/link'

const cardContent = ProductSchema.parse(text);

export const Body = () => {
  return (
    <div className="grid grid-cols-1 items-stretch md:grid-cols-2 gap-8 ">
      {cardContent.map((item, idx, arr) => {
        return  <Card
        key={item.description}
      >
        <Logo>
          <Link href={item.logo_link}>
          <Image 
            src={item.logo}
            width={100}
            height={50}
            alt="product logo"
            style={{objectFit: "contain", height: "50px", width: "50%"}}
            priority
          />
          </Link>
        </Logo>
        <div className='text-xs'>
          {item.description}
        </div>
        <ul className="mt-5 flex flex-col gap-8">
        {item.links.map((link) => {
          return <li>
            <Link className='text-base text-blue-600 font-semibold' href={link.url}>
              {link.title}
            </Link>
            <div className='text-xs'>
              {link.description}
            </div>
          </li>
        })}
        </ul>
      </Card>
      })}
    </div>
  )
}