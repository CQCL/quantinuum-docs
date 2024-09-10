import { forwardRef } from 'react'
import type { InputHTMLAttributes } from 'react'

const Card = forwardRef<
  HTMLParagraphElement,
  InputHTMLAttributes<HTMLParagraphElement>
>(({type, ...props }, ref) => {
  var class_name_val = 'flex w-full flex-col rounded-lg justify-between shadow-lg overflow-hidden p-7 pb-9 dark:bg-muted/25 bg-background';
  return (
    <div
      className={class_name_val}
      ref={ref}
    >
      <div>{props.children}</div>
    </div>
  )
})
Card.displayName = 'Card'


const Logo = forwardRef<
  HTMLParagraphElement, 
  InputHTMLAttributes<HTMLParagraphElement>
>(({type, ...props }, ref) => {
  return (
    <div className='mb-2 flex justify-left justify-items-center' ref={ref}>
      {props.children}
    </div>
  )
})
Logo.displayName = 'Logo'


export { Logo, Card }