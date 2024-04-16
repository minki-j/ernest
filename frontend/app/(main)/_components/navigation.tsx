"use client";

import { useParams, usePathname, useRouter } from "next/navigation";
import { ElementRef, useEffect, useRef, useState } from "react";

export const Navigation = () => {
  const router = useRouter();
  const params = useParams();
  const pathname = usePathname();

  return (
    <>
      <h1></h1>
    </>
  );
};
