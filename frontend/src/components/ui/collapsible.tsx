import * as React from "react"
import { cn } from "../../lib/utils"

interface CollapsibleContextValue {
  open: boolean
  onOpenChange: (open: boolean) => void
  triggerId: string
  contentId: string
}

const CollapsibleContext = React.createContext<CollapsibleContextValue | undefined>(
  undefined
)

export interface CollapsibleProps extends React.HTMLAttributes<HTMLDivElement> {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  defaultOpen?: boolean
}

const Collapsible = React.forwardRef<HTMLDivElement, CollapsibleProps>(
  ({
    open: controlledOpen,
    onOpenChange: controlledOnOpenChange,
    defaultOpen = false,
    className,
    children,
    ...props
  }, ref) => {
    const [uncontrolledOpen, setUncontrolledOpen] = React.useState(defaultOpen)
    const triggerId = React.useId()
    const contentId = React.useId()

    const open = controlledOpen ?? uncontrolledOpen
    const onOpenChange = controlledOnOpenChange ?? setUncontrolledOpen

    return (
      <CollapsibleContext.Provider
        value={{
          open,
          onOpenChange,
          triggerId,
          contentId,
        }}
      >
        <div
          ref={ref}
          className={cn("relative", className)}
          {...props}
        >
          {children}
        </div>
      </CollapsibleContext.Provider>
    )
  }
)
Collapsible.displayName = "Collapsible"

export interface CollapsibleTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean
}

const CollapsibleTrigger = React.forwardRef<HTMLButtonElement, CollapsibleTriggerProps>(
  ({ asChild, className, children, ...props }, ref) => {
    const context = React.useContext(CollapsibleContext)
    if (!context) {
      throw new Error("CollapsibleTrigger must be used within a Collapsible")
    }

    const { open, onOpenChange, triggerId, contentId } = context

    const Child = asChild ? React.Children.only(children) as React.ReactElement : 'button'
    const childProps = {
      ref,
      className: cn(
        "flex w-full justify-between items-center",
        className
      ),
      id: triggerId,
      "aria-expanded": open,
      "aria-controls": contentId,
      onClick: (e: React.MouseEvent) => {
        onOpenChange(!open)
        props.onClick?.(e as React.MouseEvent<HTMLButtonElement>)
      },
      ...props,
    }

    return React.isValidElement(Child)
      ? React.cloneElement(Child, childProps)
      : React.createElement(Child as any, { ...childProps }, children)
  }
)
CollapsibleTrigger.displayName = "CollapsibleTrigger"

export interface CollapsibleContentProps extends React.HTMLAttributes<HTMLDivElement> {}

const CollapsibleContent = React.forwardRef<HTMLDivElement, CollapsibleContentProps>(
  ({ className, children, ...props }, ref) => {
    const context = React.useContext(CollapsibleContext)
    if (!context) {
      throw new Error("CollapsibleContent must be used within a Collapsible")
    }

    const { open, contentId, triggerId } = context

    return (
      <div
        ref={ref}
        className={cn(
          "overflow-hidden transition-all duration-300",
          open ? "max-h-screen" : "max-h-0",
          className
        )}
        id={contentId}
        role="region"
        aria-labelledby={triggerId}
        hidden={!open}
        {...props}
      >
        {children}
      </div>
    )
  }
)
CollapsibleContent.displayName = "CollapsibleContent"

export { Collapsible, CollapsibleTrigger, CollapsibleContent }
