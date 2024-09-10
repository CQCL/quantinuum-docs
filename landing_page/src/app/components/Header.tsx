//@ts-ignore
import Image from 'next/image'

export const Header = () => {
  return (
    <div className="flex w-full">
      <div className="relative mx-auto flex flex-grow flex-wrap flex-col py-2">
        <div className="mb-4 mt-0 md:mt-6 flex flex-col ">
          <h1 className="text-6xl font-semibold tracking-tighter ">
            <Image
              className="md:block dark:brightness-[0.97] dark:grayscale transform "
              src="/logo.svg"
              alt="Quantinuum Logo."
              height={50}
              width={400}
              priority
            />
          </h1>
          <h2 className="text-muted-foreground mt-5 text-2xl tracking-tighter">
            Technical Documentation
          </h2>
          <h3 className="text-muted-foreground mt-2 text-base tracking-tighter">
            Explore the documentation, tutorials, and knowledge articles for our software, 
            toolkits and H-Series hardware at the links below
          </h3>
        </div>
      </div>
      <div className='text-muted-foreground flex-grow h-64 flex flex-col items-center justify-center mix-blend-overlay'>
        <Image
          className="lg:ml-4 mt-10 hidden md:block dark:brightness-[0.97] dark:grayscale dark:invert transform "
          src="/q.svg"
          alt="Quantinuum Hero"
          objectFit="contain"
          height={100}
          width={200}
          priority
        />
      </div>
    </div>
  )
}
