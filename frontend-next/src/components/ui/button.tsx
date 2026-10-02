import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
  {
    variants: {
      variant: {
        default:
          "bg-blue-600 text-white hover:bg-blue-700 shadow-md shadow-blue-500/20",
        destructive:
          "bg-red-600 text-white hover:bg-red-700 shadow-md shadow-red-500/20",
        outline:
          "border border-slate-700/60 bg-slate-900/40 hover:bg-slate-800 text-slate-200 hover:text-white backdrop-blur-sm",
        secondary:
          "bg-slate-800 text-slate-100 hover:bg-slate-700 border border-slate-700/40",
        ghost:
          "hover:bg-slate-800/60 text-slate-300 hover:text-white",
        link:
          "text-blue-400 underline-offset-4 hover:underline",
        gradient:
          "bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 text-white shadow-lg shadow-blue-500/25 hover:opacity-95 hover:shadow-cyan-500/25",
        emerald:
          "bg-emerald-600 text-white hover:bg-emerald-700 shadow-md shadow-emerald-500/20",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-11 rounded-lg px-6 text-base font-semibold",
        icon: "h-9 w-9 rounded-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
