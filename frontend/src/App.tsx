import { Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar'
import Footer from './components/Footer'
import ChatPanel from './components/ChatPanel'
import ChatShelf from './components/ChatShelf'
import Home from './pages/Home'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import About from './pages/About'
import Login from './pages/Login'
import CreateAccount from './pages/CreateAccount'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <div className="app">
      <NavBar />
      <main className="main">
        <ChatShelf />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:id" element={<ProductDetail />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/create-account" element={<CreateAccount />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
      <ChatPanel />
    </div>
  )
}
