import React from 'react'
import {createRoot} from "react-dom/client" 
import { MainNavigation } from "./components/navmenu/MainNavigation";

  (() => {
    const mountElement = document.querySelector('.nexus-nav')
    if (!mountElement) return
    const renderIn = document.createElement('div')
    mountElement.appendChild(renderIn)
  
    const root = createRoot(renderIn)

    root.render(
      <div className="use-tailwind">  <div className="font-inter antialiased"><MainNavigation activePath=""></MainNavigation> </div></div>
    )
  })()

