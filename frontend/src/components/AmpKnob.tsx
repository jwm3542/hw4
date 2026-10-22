import { KeyboardEvent } from 'react'
import { useVolume } from '../eleven'

// A Marshall-style amp knob. Click or arrow keys to turn; 11 unlocks metal mode.
export default function AmpKnob() {
  const { volume, setVolume } = useVolume()
  const turn = (v: number) => setVolume(Math.min(11, Math.max(1, v)))
  const onKey = (e: KeyboardEvent) => {
    if (e.key === 'ArrowUp' || e.key === 'ArrowRight') turn(volume + 1)
    else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') turn(volume - 1)
    else if (e.key === 'End') turn(11)
    else if (e.key === 'Home') turn(1)
    else return
    e.preventDefault()
  }
  // 1 -> -135deg ... 10 -> +135deg; 11 goes one notch past the end of the dial.
  const angle = -135 + ((volume - 1) / 9) * 270

  return (
    <div className="amp">
      <div className="amp-plate">
        <span className="amp-brand">Campus Customs</span>
        <div
          className="knob"
          role="slider"
          tabIndex={0}
          aria-label="Shop volume (turn it to 11)"
          aria-valuemin={1}
          aria-valuemax={11}
          aria-valuenow={volume}
          aria-valuetext={volume === 11 ? '11: metal mode' : String(volume)}
          onClick={() => turn(volume === 11 ? 7 : volume + 1)}
          onKeyDown={onKey}
        >
          <div className="knob-cap" style={{ transform: `rotate(${angle}deg)` }}>
            <span className="knob-pointer" />
          </div>
          {Array.from({ length: 11 }, (_, i) => (
            <span
              key={i}
              className={`knob-num ${i + 1 === volume ? 'on' : ''} ${i === 10 ? 'eleven-num' : ''}`}
              style={{ transform: `rotate(${-135 + (i / 9) * 270}deg) translateY(-46px) rotate(${135 - (i / 9) * 270}deg)` }}
            >
              {i + 1}
            </span>
          ))}
        </div>
        <span className="amp-label">Volume</span>
      </div>
      <p className="amp-caption">
        {volume === 11 ? '🤘 Metal mode. It’s one louder. Click to bring it back to 7.' : 'Most stores go to ten. Click to turn it up.'}
      </p>
    </div>
  )
}
