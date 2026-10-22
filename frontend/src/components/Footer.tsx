import { STORE } from '../content'
import AmpKnob from './AmpKnob'

// The building's story, told like the brass plaque by the door.
const ERAS = [
  { year: '1880s', text: 'Brick storefront goes up on Broadway' },
  { year: '1975', text: 'Campus Customs opens the doors' },
  { year: '1984', text: 'Amps in the back room go to 11' },
  { year: 'Today', text: 'Still here, still Bulldog Blue' },
]

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="plaque">
          <p className="plaque-title">The Shop at 57 Broadway</p>
          <ol className="timeline">
            {ERAS.map(e => (
              <li key={e.year}>
                <span className="timeline-year">{e.year}</span>
                <span>{e.text}</span>
              </li>
            ))}
          </ol>
        </div>
        <AmpKnob />
        <div className="footer-contact">
          <strong>{STORE.name}</strong>
          <p>{STORE.address}</p>
          <p>
            <a href={`tel:${STORE.phone.replace(/\D/g, '')}`}>{STORE.phone}</a>
          </p>
          <p>
            <a href={`mailto:${STORE.email}`}>{STORE.email}</a>
          </p>
        </div>
      </div>
      <p className="copyright">© 2026 Yale Bulldog Blue by Campus Customs</p>
    </footer>
  )
}
