import {
  DocsFooter,
  DocsNavBar,
  DocsTripleCard,
  DocsHeaderWrapper,
  DocsHeaderLeft,
  DocsHeaderRight,
  DocsHeaderSubtitle,
  Button,
  DocsPageLayout,
  CardTitle,
  Card,
  CardHeader,
  CardDescription,
  CardContent,
} from "@cqcl/quantinuum-ui";
import { LifeBuoyIcon, BookIcon } from "lucide-react";
import Image from "next/image";
import { HSeriesLogo } from "./HSeriesLogo";
import { ComponentProps } from "react";
import { QLogo } from "./Q";
import { QuantinuumLogo } from "./QuantinuumLogo";
import { NexusLogo } from "./NexusLogo";
import { LambeqLogo } from "./LambeqLogo";
import { InquantoLogo } from "./InquantoLogo";
import { TKETLogo } from "./TKETLogo";


const productsConfig = [
  {name: "H-Series", link:"h-series", description: `Quantinuum's QCCD ion-trap hardware, the world's highest peforming quantum computer.`, links: [{
    title: 'H-Series User Guide',
    link: 'h-series/user_guide/hardware_user_guide/access',
    subtitle: "Explore how to use the industry's leading quantum processors"
  },
  {
    title: 'Getting started with H-Series',
    link: 'h-series/trainings/getting_started/index.html',
    subtitle: "Find the latest technical documentation and additional resources."
  }], logo: <HSeriesLogo width={150 * 1.5} height={16 * 1.5}></HSeriesLogo>, },

  {name: "Nexus", link:"nexus", description: `Cloud platform connecting users with hardware and compilation services, alongside associated data.`, links: [{
    title: 'Apply for Access',
    link: 'https://nexus.quantinuum.com/signup',
    subtitle: "Register your interest in becoming an early adopter of Quantinuum Nexus."
  }, 
  {
    title: 'Tutorials and Documentation',
    link: 'https://docs.quantinuum.com/nexus/examples/overview.html',
    subtitle: "Read the full Quantinuum Nexus documentation."
  }], logo:  <NexusLogo variant="horizontal"  className="h-10 w-48 -mt-1"  />, },

  {name: "TKET",link:"tket", logo:<TKETLogo className="h-8 w-32" ></TKETLogo>,  description: `Quantum computing toolkit and optimizing compiler`, links: [{
    title: 'Get Started with TKET',
    link: 'tket/user-guide/',
    subtitle: "Getting started tutorial showing basic usage of pytket"
  },
  {
    title: 'Documentation for TKET',
    link: 'tket',
    subtitle: "Overview of all TKET documentation including the user guide, API docs, and developer blog"
  }],  },

  {name: "InQuanto",  link:"inquanto", description: `Toolkit for complex molecular and materials simulations`, links: [{
    title: 'User Manual',
    link: 'inquanto/manual/howto.html',
    subtitle: "Learn how to use the InQuanto package"
  },
  {
    title: 'Tutorials and Examples',
    link: 'inquanto/tutorials/tutorial_overview.html',
    subtitle: "Hands-on tutorials and examples to get started with running quantum chemical calculations."
  }], logo:  <InquantoLogo className="h-8 w-56"></InquantoLogo>, },

  {name: "Lambeq", link:"lambeq", description: `Α Python toolkit for quantum natural language processing`, links: [{
    title: 'Get Started with λambeq',
    link: 'lambeq/intro.html',
    subtitle: "Learn how to convert your text into quantum circuits and train quantum models to solve language-related tasks"
  },
  {
    title: 'Tutorials and Documentation',
    link: 'lambeq/index.htmll',
    subtitle: "Find the latest technical documentation and additional resources"
  }], logo:  <LambeqLogo className="h-8 w-48"></LambeqLogo>, },
]


const navConfig = {
  navTextLinks: productsConfig.map(item => ({
    title: item.name,
        href: item.link,
        pathMatch: "",
  })) ,
  navProductName: "Docs",
  navIconLinks: [],
}

const footerConfig = {
  columns: [
    {
      title: "Products",
      items: [
        { name: "H-Series", href: "https://docs.quantinuum.com/h-series" },
        { name: "Nexus", href: "https://docs.quantinuum.com/nexus" },
        { name: "InQuanto", href: "https://docs.quantinuum.com/inquanto" },
      ],
    },
    {
      title: "Opensource",
      items: [
        { name: "TKET", href: "https://docs.quantinuum.com/tket" },
        { name: "λambeq", href: "https://docs.quantinuum.com/lambeq" },
      ],
    },
    {
      title: "Quantinuum",
      items: [
        { name: "About", href: " https://www.quantinuum.com/about" },
        { name: "Research", href: "https://www.quantinuum.com/publications" },
        { name: "Events", href: "https://www.quantinuum.com/events" },
      ],
    },
  ],
  subtitle: "",
};


const helpSectionConfig = [
  {
    title: "Get in touch for support",
    image_description: "Support Icon",
    icon: LifeBuoyIcon,
    link: "mailto:qcsupport@quantinuum.com",
    description: "Need help? Contact our support team here",
   
  },
  {
    title: "Publications",
    image_description: "Publications Icon",
    icon: BookIcon,
    description: "Find our latest research publications here",
    link: "https://quantinuum.com/publications",
  },
];

export default function Home() {
  return (
    <>
      <DocsNavBar activePath="/" {...navConfig} />
      <DocsPageLayout>
        <DocsHeaderWrapper>
          <DocsHeaderLeft>
            <QuantinuumLogo className="-mb-1 w-[18rem] md:w-[32rem] h-10 md:h-16 dark:invert" />
            <DocsHeaderSubtitle className="mb-4">
            Technical Documentation
            </DocsHeaderSubtitle>
            <p className="text-muted-foreground">
            Explore the documentation, tutorials, and knowledge articles for our software, toolkits and H-Series hardware at the links below.
            </p>
            
          </DocsHeaderLeft>
          <DocsHeaderRight className="hidden md:flex">
            <QLogo className="w-64 h-64 ml-48"></QLogo>
            
          </DocsHeaderRight>
        </DocsHeaderWrapper>
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-8">
    
      {productsConfig.map(product => {
        return <Card  className="px-0 md:px-4 py-4" key={product.name}>
          <CardHeader >
            <a  href={product.link} className="transition hover:opacity-50 scale-[75%] md:scale-[100%]">
            {product.logo}
            </a>
            <div className="h-1"></div>
            <CardDescription >{product.description}</CardDescription>
            <div className="h-5"></div>
            <ul className="flex flex-col gap-6">
              {product.links.map(({link,subtitle, title}) => {
                return <li key={title}>
                  <a  className="font-semibold tracking-tight text-blue-600 dark:text-blue-300" href={link}>{title}</a>
                  <p>{subtitle}</p>
                </li>
              })}</ul>
  
          </CardHeader>
        </Card>
     
      })}
      
      </section>
      <div className="my-24 grid grid-cols-1 flex-grow gap-8 md:grid-cols-2">
      {helpSectionConfig.map((item) => {
        return (
          <a href={item.link}             key={item.title}>
          <Card
      className="hover:bg-muted transition"
          >
                <CardHeader>

                  <item.icon className="w-6 h-6 mb-3 inline" aria-label={item.image_description}></item.icon>
                
            
      <CardTitle className="text-[1rem] font-semibold inline-block">       {item.title}</CardTitle>
      <CardDescription>{item.description}</CardDescription>
      </CardHeader>
          </Card>
          </a>
        );
      })}
      </div> 
      <DocsFooter {...footerConfig} />
      </DocsPageLayout>
    </>
  );
}
