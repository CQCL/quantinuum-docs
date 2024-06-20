
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
  //@ts-ignore
} from '@cqcl/quantinuum-ui'

import { Link, links } from './config'

export const Navigation = (props: {
  activePath: string
  linkComponent: Link
}) => {
  const isActivePath = (activePath: string, path: string) => {
    return activePath.startsWith(path)
  }
  return (
    <NavigationMenu className="place-self-center sm:block">
      <NavigationMenuList className="hidden md:flex">
        {links.map((item) => {
          return (
            <NavigationMenuItem key={item.title}>
              <NavigationMenuLink
                className={navigationMenuTriggerStyle()}
                asChild
                active={isActivePath(props.activePath, item.pathMatch)}
              >
                <props.linkComponent href={item.href}>
                  {item.title}
                </props.linkComponent>
              </NavigationMenuLink>
            </NavigationMenuItem>
          )
        })}
      </NavigationMenuList>
    </NavigationMenu>
  )
}
