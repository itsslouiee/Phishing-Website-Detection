import { Detector } from '@/components/detector'
import { Footer } from '@/components/footer'
import { Header } from '@/components/header'
import { Workflow } from '@/components/workflow'

/** Page order is fixed: Header → URL analysis → Model evaluation → Workflow → Footer. */
export default function Page() {
  return (
    <>
      <Header />
      <main>
        <Detector />
        <Workflow />
      </main>
      <Footer />
    </>
  )
}
