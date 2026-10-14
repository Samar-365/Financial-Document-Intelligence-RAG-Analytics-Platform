import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-semibold ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E63946] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98] cursor-pointer",
  {
    variants: {
      variant: {
        default:
          "btn-primary-wine",
        primary:
          "btn-primary-wine",
        destructive:
          "bg-red-700 text-white hover:bg-red-800 shadow-md shadow-red-500/20",
        outline:
          "btn-secondary-wine",
        secondary:
          "btn-secondary-wine",
        ghost:
          "hover:bg-[rgba(184,29,36,0.15)] text-slate-300 hover:text-white",
        link:
          "text-[#E63946] underline-offset-4 hover:underline",
        gradient:
          "btn-primary-wine",
        emerald:
          "bg-emerald-600 text-white hover:bg-emerald-700 shadow-md shadow-emerald-500/20",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-11 rounded-lg px-6 text-base font-bold",
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
