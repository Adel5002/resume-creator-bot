import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { User } from "lucide-react";

export default function MainPage({ username = "username", avatarUrl }) {
  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-900 text-white p-6 flex flex-col">
      {/* Top Bar */}
      <div className="flex items-center justify-between mb-10">
        {/* Username */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-xl font-semibold tracking-wide"
        >
          @{username}
        </motion.div>

        {/* Avatar */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="w-12 h-12 rounded-full overflow-hidden border border-white/20 shadow-lg"
        >
          {avatarUrl ? (
            <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-zinc-700 flex items-center justify-center">
              <User className="w-6 h-6 text-white/70" />
            </div>
          )}
        </motion.div>
      </div>

      {/* Main Content */}
      <div className="flex flex-col items-center text-center mt-10">
        <motion.h1
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold mb-4 drop-shadow-lg"
        >
          Создай идеальное резюме
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-lg text-white/70 max-w-xl"
        >
          Твой ИИ‑ассистент поможет создать или улучшить профессиональное резюме за пару минут.
        </motion.p>

        <div className="flex flex-col gap-4 w-full max-w-xl mt-14">
          {/* Full-width Create Button */}
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button className="w-full py-8 text-xl rounded-2xl shadow-lg">
              Создать резюме с нуля
            </Button>
          </motion.div>

          {/* Full-width Edit Button */}
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button className="w-full py-8 text-xl rounded-2xl shadow-lg">
              Редактировать резюме
            </Button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
