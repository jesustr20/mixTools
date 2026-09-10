import PdfToJpgPanel from './components/PdfToJpgPanel'

function App() {
  return (
    <main className="min-h-screen bg-paper py-11 text-graphite">
      <div className="mx-auto max-w-[920px] px-[52px]">
        <header className="mb-7">
          <h1 className="m-0 mb-1.5 text-[23px] font-bold text-ink">PDF → JPG</h1>
          <p className="m-0 max-w-[58ch] text-sm leading-normal text-graphite-soft">
            Convierte un PDF a imágenes JPG — una imagen por página.
          </p>
        </header>
        <PdfToJpgPanel />
      </div>
    </main>
  )
}

export default App
