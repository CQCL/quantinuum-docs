import { Navigation } from './NavigationMenu'
import React, { ComponentProps } from 'react'
import { Link } from './config'
import { ModeSelector } from './ModeSelector'
import { QuantinuumLogo } from '../QuantinuumLogo'
import { GithubIcon, SlackIcon } from 'lucide-react'
import { FaGithub, FaSlack, FaStackExchange } from 'react-icons/fa'
import {IoLogoSlack} from 'react-icons/io'
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
          <div className="whitespace-nowrap flex items-center gap-2">
          <a href="https://docs.quantinuum.com/" aria-label='Quantinuum Docs' title="Quantinuum Docs"  className='hover:cursor-pointer hover:opacity-50 transition'>
            <div className='hidden sm:block'><QuantinuumLogo></QuantinuumLogo>
            </div>
            <div className='block sm:hidden'>
             
              <QuantinuumLogo/>
            
            </div>
            </a>
            {/* <div className="text-muted-foreground text-xs font-medium flex items-center gap-1.5">
              <div>|</div><div>H-Series</div>
            </div> */}
          </div>
          <Link href="/" className="ml-4 mr-4 flex items-center space-x-2">
            <span className="hidden font-bold">Quantinuum</span>
          </Link>
          <Navigation activePath={props.activePath} linkComponent={Link} />
        </div>
      </div>
    </div>
  )
}
