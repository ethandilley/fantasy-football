import styles from './StatusPill.module.css'

export function StatusPill({ online }) {
  return (
    <div className={`${styles.pill} ${online ? styles.online : styles.offline}`}>
      <span className={styles.dot} />
      {online ? 'platform online' : 'platform offline'}
    </div>
  )
}
