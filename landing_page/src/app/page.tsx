import { Separator } from '@cqcl/quantinuum-ui'
import { Footer } from './components/Footer'
import Link from 'next/link'
import { MainNavigation } from './components/navmenu/MainNavigation'
import { Header } from './components/Header'
import { Body } from './components/Body'


export default function Home() {
  return (
    <div className="absolute top-0 z-30 flex w-screen flex-col items-center">
      <MainNavigation activePath="/" linkComponent={Link} />
      <div
        className="container mx-auto py-6 md:py-4"
        style={{ objectFit: 'contain' }}
      >
        <div className="mt-4 flex flex-col sm:items-center">
          <Header />
        </div>
        <div className="my-6"></div>
        <Body />
        <div className="my-12"></div>
        <Separator></Separator>
        <div className="my-12"></div>
        <Footer />
        <div className="my-16"></div>
      </div>
    </div>
  )
}
