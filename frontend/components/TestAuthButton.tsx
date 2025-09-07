'use client';

import React, { useState } from 'react';

function TestAuthModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-xl max-w-md w-full p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">測試登入</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Email
            </label>
            <input
              type="email"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              密碼
            </label>
            <input
              type="password"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-medium"
          >
            登入
          </button>
        </div>
      </div>
    </div>
  );
}

export function TestAuthButton() {
  const [showModal, setShowModal] = useState(false);

  console.log('TestAuthButton rendered, showModal:', showModal);

  return (
    <>
      <button
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          console.log('Test Login button clicked!', e);
          alert('按鈕被點擊了！');
          setShowModal(true);
        }}
        style={{ zIndex: 9999 }}
        className="px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800 transition-all duration-200 font-medium"
      >
        測試登入
      </button>
      
      {console.log('About to render modal, showModal:', showModal)}
      {showModal && (
        <>
          {console.log('Rendering TestAuthModal')}
          <TestAuthModal 
            isOpen={showModal} 
            onClose={() => {
              console.log('Closing modal');
              setShowModal(false);
            }} 
          />
        </>
      )}
    </>
  );
}