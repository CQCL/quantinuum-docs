import { Navigation } from './NavigationMenu'
import React, { ComponentProps } from 'react'
import { Link, navConfig } from './config'
import { QuantinuumLogo } from './QuantinuumLogo'
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
            <div className="text-muted-foreground text-xs font-medium flex items-center gap-1.5">
              <div>|</div><div>{navConfig.navProductName}</div>
            </div>
          </div>
          <Link href="/" className="ml-4 mr-4 flex items-center space-x-2">
            <span className="hidden font-bold">Quantinuum</span>
          </Link>
          <Navigation activePath={props.activePath} linkComponent={Link} />
        </div>

        <div className="flex items-center">
          <div className="flex items-center gap-2">
            {navConfig.navIconLinks.map(link => {
                return <Link href={link.href} target='_blank' key={link.title}>
               <img src={link.iconImageURL} className='w-6 h-6 hover:opacity-70 transition'></img>
             </Link>
            
            })}
           
           
          </div>
          {/* <div className="mx-2 ml-4">
            <ModeSelector />
          </div> */}
        </div>
      </div>
    </div>
  )
}
