// Export all components from a single entry point
// This simplifies imports: instead of:
//   import Navbar from './components/Navbar'
//   import Footer from './components/Footer'
// You can now do:
//   import { Navbar, Footer } from './components'

export { default as Navbar } from './Navbar';
export { default as MegaMenu } from './MegaMenu';
export { default as SearchPanel } from './SearchPanel';
export { default as CartPanel } from './CartPanel';
export { default as Hero } from './Hero';
export { default as ProductCard } from './ProductCard';
export { default as Footer } from './Footer';

// Export as named object for convenience
export * as Components from './index';
