'use client';

import React, { useState } from 'react';

export function TestSimpleButton() {
  const [clicked, setClicked] = useState(false);

  const handleClick = () => {
    console.log('TestSimpleButton: 點擊事件觸發!');
    setClicked(!clicked);
    alert('測試按鈕被點擊了!');
  };

  return (
    <button
      onClick={handleClick}
      style={{
        padding: '8px 16px',
        backgroundColor: clicked ? 'green' : 'blue',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '14px'
      }}
    >
      簡單測試按鈕 {clicked ? '✅' : '❌'}
    </button>
  );
}