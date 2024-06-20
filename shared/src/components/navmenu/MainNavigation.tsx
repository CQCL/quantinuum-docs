import { Navigation } from './NavigationMenu'
import React, { ComponentProps } from 'react'
import { Link } from './config'

import { QuantinuumLogo } from './QuantinuumLogo'
import { FaGithub, FaSlack, FaStackExchange } from 'react-icons/fa'
import { MobileMenu } from './MobileMenu'
export const MainNavigation = (props: {
  activePath: string
  linkComponent?: Link
}) => {
  const Link = props.linkComponent
    ? props.linkComponent
    : (props: ComponentProps<'a'>) => <a {...props}></a>
  return (
    <div className="bg-background text-foreground border-border sticky top-0 z-[100] w-full border-b text-sm">
      <div className=" bg-background container flex h-14 items-center justify-between">
        <div className="mr-4 flex items-center">
        <div className='block md:hidden mr-3'>
            <MobileMenu></MobileMenu>
            </div>
          <div className=" whitespace-nowrap flex items-center gap-2">
            <QuantinuumLogo></QuantinuumLogo>
            <div className="text-muted-foreground text-xs font-medium">
              | TKET
            </div>
          </div>
          <Link href="/" className="ml-4 mr-4 flex items-center space-x-2">
            <span className="hidden font-bold">Quantinuum</span>
          </Link>
          <Navigation activePath={props.activePath} linkComponent={Link} />
        </div>

        <div className="flex items-center">
          <div className="flex items-center gap-3">
            <Link href="https://github.com/CQCL/tket" target="_blank">
              <FaGithub className="text-foreground hover:text-muted-foreground h-[1.5rem] w-[1.5rem] transition" />
            </Link>
            <Link href="https://tketusers.slack.com/" target="_blank">
              <FaSlack className="text-foreground hover:text-muted-foreground h-6 w-6 transition" />
            </Link>
            <Link
              href="https://quantumcomputing.stackexchange.com/questions/tagged/pytket"
              target="_blank"
            >
              <FaStackExchange className="text-foreground hover:text-muted-foreground h-5 w-5 transition"></FaStackExchange>
            </Link>
           
          </div>
          {/* <div className="mx-2 ml-4">
            <ModeSelector />
          </div> */}
        </div>
      </div>
    </div>
  )
}
