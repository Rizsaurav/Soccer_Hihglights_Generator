"use client"

import type { ReactNode } from "react"
import { useState } from "react"
import { motion } from "framer-motion"

interface FloatingActionButtonProps {
  icon: ReactNode
  label: string
  href: string
  color?: string
  textColor?: string
}

export default function FloatingActionButton({
  icon,
  label,
  href,
  color = "bg-white",
  textColor = "text-black",
}: FloatingActionButtonProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.a
      href={href}
      className={`flex items-center gap-2 ${color} ${textColor} rounded-full shadow-lg overflow-hidden`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      initial={{ width: "3rem" }}
      animate={{ width: isHovered ? "auto" : "3rem" }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <div className="w-12 h-12 flex items-center justify-center flex-shrink-0">{icon}</div>
      {isHovered && (
        <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="pr-4 whitespace-nowrap font-medium">
          {label}
        </motion.span>
      )}
    </motion.a>
  )
}
