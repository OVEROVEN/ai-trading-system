'use client';

import React from 'react';
import { useLanguage, Language } from '../contexts/LanguageContext';

const languages: { code: Language; name: string; flag: string }[] = [
  { code: 'en', name: 'EN', flag: '🇺🇸' },
  { code: 'zh-TW', name: 'TW', flag: '🇹🇼' },
];

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="flex space-x-1">
      {languages.map((lang) => (
        <button
          key={lang.code}
          onClick={() => setLanguage(lang.code)}
          className={`
            px-2 py-1 text-sm rounded transition-colors
            ${language === lang.code 
              ? 'bg-blue-600 text-white' 
              : 'text-slate-300 hover:text-white hover:bg-slate-700'
            }
          `}
          title={lang.name}
        >
          {lang.flag}
        </button>
      ))}
    </div>
  );
}