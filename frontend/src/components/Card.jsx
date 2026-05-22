import styles from './Card.module.css'

export function Card({ title, children, full = false }) {
  return (
    <div className={`${styles.card} ${full ? styles.full : ''}`}>
      {title && <div className={styles.title}>{title}</div>}
      {children}
    </div>
  )
}
