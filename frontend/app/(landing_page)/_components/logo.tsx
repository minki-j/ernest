import Image from "next/image";
import { Poppins } from "next/font/google";

import { cn } from "@/lib/utils";

const font = Poppins({
  subsets: ["latin"],
  weight: ["400", "600"]
});

export const Logo = () => {
  return (
    <div className="hidden md:flex items-center gap-x-2">
      <div className="rounded-full overflow-hidden">
        <Image
          src="/logo.png"
          height="50"
          width="50"
          alt="Logo"
          className="circle-icon"
        />
      </div>
      <p className={cn("font-semibold", font.className)}>
        Recipeasy
      </p>
    </div>
  )
}