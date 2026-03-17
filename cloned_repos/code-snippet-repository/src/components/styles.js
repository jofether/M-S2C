export const styles = `
  * { box-sizing: border-box; }
  
  .code-editor {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  }
  .code-window {
    background: linear-gradient(to bottom, #1e293b, #0f172a);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
  }
  .header-bar {
    background: linear-gradient(90deg, #1e293b, #0e7490);
  }
  .line-hover:hover {
    background: rgba(255, 255, 255, 0.08);
    cursor: text;
  }
  .snippet-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
  }
  .snippet-card:hover {
    transform: translateX(4px) translateY(-2px);
    box-shadow: 0 8px 24px rgba(6, 182, 212, 0.15);
  }
  .snippet-card.active {
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.3), rgba(59, 130, 246, 0.1)) !important;
    border-color: rgba(6, 182, 212, 0.8) !important;
    box-shadow: 0 8px 32px rgba(6, 182, 212, 0.2);
  }
  .category-btn {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
  }
  .category-btn:hover {
    transform: translateY(-2px);
  }
  .category-btn.active {
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.3), rgba(59, 130, 246, 0.2)) !important;
    border-color: rgba(6, 182, 212, 0.8) !important;
  }
  
  .floating-card {
    animation: float 6s ease-in-out infinite;
  }
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
  }
  
  .pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  .glow {
    animation: glow 2s ease-in-out infinite;
  }
  @keyframes glow {
    0%, 100% { box-shadow: 0 0 5px rgba(6, 182, 212, 0.3), inset 0 0 10px rgba(6, 182, 212, 0.1); }
    50% { box-shadow: 0 0 20px rgba(6, 182, 212, 0.6), inset 0 0 20px rgba(6, 182, 212, 0.2); }
  }
  
  .badge {
    animation: slideIn 0.3s ease-out forwards;
  }
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  .gradient-text {
    background-image: linear-gradient(90deg, #06b6d4, #0ea5e9, #3b82f6, #8b5cf6);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  
  ::-webkit-scrollbar {
    width: 6px;
  }
  ::-webkit-scrollbar-track {
    background: rgba(148, 163, 184, 0.1);
  }
  ::-webkit-scrollbar-thumb {
    background: rgba(6, 182, 212, 0.5);
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(6, 182, 212, 0.8);
  }
  
  .tab-indicator {
    position: absolute;
    bottom: 0;
    height: 3px;
    background: linear-gradient(90deg, #06b6d4, #0ea5e9, #3b82f6);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 2px;
  }
`;
