export const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const getConnectionQualityColor = (quality) => {
  switch(quality) {
    case 'excellent': return 'bg-emerald-500';
    case 'good': return 'bg-blue-500';
    case 'fair': return 'bg-amber-500';
    case 'poor': return 'bg-red-500';
    default: return 'bg-slate-500';
  }
};

export const getConnectionQualityIcon = (quality) => {
  switch(quality) {
    case 'excellent': return '█████';
    case 'good': return '████░';
    case 'fair': return '██░░░';
    case 'poor': return '█░░░░';
    default: return '░░░░░';
  }
};
