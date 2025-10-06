import React from "react";
import { FaMoon, FaSun } from "react-icons/fa";

export default function ThemeToggle({ theme, setTheme }) {
  const toggleTheme = () => setTheme(theme === "dark" ? "light" : "dark");

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-full border border-gray-600 hover:bg-gray-700 transition-colors"
      title="Toggle Theme"
    >
      {theme === "dark" ? (
        <FaSun className="text-yellow-400" size={18} />
      ) : (
        <FaMoon className="text-gray-800" size={18} />
      )}
    </button>
  );
}
