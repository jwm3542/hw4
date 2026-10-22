import { ABOUT, STORE } from '../content'

export default function About() {
  return (
    <section className="container prose">
      <h1>{ABOUT.title}</h1>
      {ABOUT.paragraphs.map((p, i) => (
        <p key={i}>{p}</p>
      ))}
      <h2>{ABOUT.returnsTitle}</h2>
      <ul>
        {ABOUT.returns.map(r => (
          <li key={r}>{r}</li>
        ))}
      </ul>
      <h2>Find us</h2>
      <p>
        {STORE.address}
        <br />
        <a href={`tel:${STORE.phone.replace(/\D/g, '')}`}>{STORE.phone}</a> ·{' '}
        <a href={`mailto:${STORE.email}`}>{STORE.email}</a>
      </p>
    </section>
  )
}
