"""
constants.py — ثوابت العرض الخاصة بلوحة الإدارة.
"""

# ألوان شارة فئة المانح (كلاسات Tailwind) — تُرسل للواجهة كـ JSON
CATEGORY_STYLES = {
    "البلاتينية":     {"bg": "bg-slate-100",  "text": "text-slate-600",  "border": "border-slate-300",    "dot": "bg-slate-400"},
    "الألماسية":      {"bg": "bg-sky-50",     "text": "text-sky-600",    "border": "border-sky-300",      "dot": "bg-sky-400"},
    "الذهبية":        {"bg": "bg-amber-50",   "text": "text-amber-600",  "border": "border-amber-300",    "dot": "bg-amber-400"},
    "الفضية":         {"bg": "bg-gray-100",   "text": "text-gray-500",   "border": "border-gray-300",     "dot": "bg-gray-400"},
    "البرونزية":      {"bg": "bg-[#fdf3e7]",  "text": "text-[#8B4513]",  "border": "border-[#CD7F32]/40", "dot": "bg-[#CD7F32]"},
    "الدرجة الأولى":  {"bg": "bg-teal-50",    "text": "text-teal-700",   "border": "border-teal-300",     "dot": "bg-teal-500"},
    "الدرجة الثانية": {"bg": "bg-cyan-50",    "text": "text-cyan-700",   "border": "border-cyan-300",     "dot": "bg-cyan-500"},
    "الدرجة الثالثة": {"bg": "bg-lime-50",    "text": "text-lime-700",   "border": "border-lime-300",     "dot": "bg-lime-500"},
    "جديدة":          {"bg": "bg-[#F3FCF6]",  "text": "text-[#1B8354]",  "border": "border-[#88D8AD]",    "dot": "bg-[#1B8354]"},
}
