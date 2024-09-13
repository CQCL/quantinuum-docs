import Link from 'next/link'
import { QuantinuumLogo } from './QuantinuumLogo'

const columns = [
  {
    title: "Legal",
    items: [
      {name: "Terms & Conditions", href: "https://www.quantinuum.com/terms-conditions"},
      {name: "Privacy Policy", href: "https://www.quantinuum.com/terms-conditions"},
      {name: "Cookie Notice", href: "https://www.quantinuum.com/cookie-notice"}

    ]
  },
  {
    title: 'Solutions',
    items: [
      { name: 'Nexus', href: 'https://docs.quantinuum.com/nexus' },
      { name: 'TKET', href: 'https://docs.quantinuum.com/tket' },
      { name: 'InQuanto', href: 'https://docs.quantinuum.com/inquanto' },
      { name: 'lambeq', href: 'https://docs.quantinuum.com/lambeq' },
    ],
  },
  {
    title: 'Hardware',
    items: [
      { name: 'H-Series', href: 'https://docs.quantinuum.com/h-series' },
      { name: 'Get Access', href: 'https://www.quantinuum.com/hardware#access' },
    ],
  },
  {
    title: "Quantinuum",
    items: [
      { name: 'About', href: ' https://www.quantinuum.com/about' },
      { name: 'Research', href: 'https://www.quantinuum.com/publications' },
      { name: 'Events', href: 'https://www.quantinuum.com/events' },
    ],
  },
]

export const Footer = () => {
  return (
    <footer className="text-muted-foreground flex w-full flex-col justify-between md:items-start lg:flex-row ">
      <div className="mb-12 md:mb-0">
        <div className="-mt-4">
          <Link href="https://www.quantinuum.com/" className='hover:opacity-75 transition'>
            <QuantinuumLogo />
          </Link>
        </div>
        <p className="max-w-[24rem] text-xs leading-5">
          ©{new Date().getFullYear()} Quantinuum Ltd. All rights reserved.{' '}
        </p>
      </div>
      <div className="grid grid-cols-1 gap-16 md:grid-cols-4 md:gap-24">
        {columns.map((col) => {
          return (
            <div key={col.title} className="flex flex-col md:items-end">
              <span className="text-foreground text-left text-[0.675rem] font-semibold uppercase tracking-wide md:text-right">
                {col.title}
              </span>
              <ul className="mt-3 flex flex-col gap-2 md:text-right">
                {col.items.map((item) => {
                  return (
                    <li key={item.name}>
                      <a
                        className="text-muted-foreground text-[0.85rem] font-medium"
                        href={item.href}
                      >
                        {item.name}
                      </a>
                    </li>
                  )
                })}
              </ul>
            </div>
          )
        })}
      </div>
    </footer>
  )
}
