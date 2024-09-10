'use client'
import { PropsWithChildren } from 'react'

import { cn } from '@cqcl/quantinuum-ui'

export const AnimatedBox = (
  props: PropsWithChildren<{ className?: string }>
) => {
  // const ref = React.useR
  return (
    <div
      className={cn(
        'border-border relative flex-grow overflow-hidden rounded border ',
        props.className
      )}
    >
      <div className="absolute bottom-0 left-0 right-0 top-0 z-10 flex items-center justify-center">
        <div
          className="animate-spin-border animate flex items-center justify-center rounded"
          style={{ width: '120rem', height: '80rem' }}
        >
          <div
            style={{
              background: `conic-gradient(${'#999'} 0deg, transparent 270deg)`,
              width: '120rem',
              height: '800rem',
            }}
            className="transform rounded "
          ></div>
        </div>
      </div>

      <div className="bg-background absolute bottom-0 left-0 right-0 top-0 z-20 m-px"></div>
      <div className="relative z-30 m-px">{props.children}</div>
    </div>
  )
}
