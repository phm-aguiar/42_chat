interface AvatarProps {
  login: string
  imageUrl?: string
}

export default function Avatar({ login, imageUrl }: AvatarProps) {
  const initials = login.slice(0, 2).toUpperCase()

  return (
    <div
      className="avatar-42 shrink-0"
      title={login}
    >
      {imageUrl ? (
        <img
          src={imageUrl}
          alt={login}
          className="w-full h-full object-cover"
          onError={(e) => {
            // Fallback para iniciais se imagem falhar
            const target = e.currentTarget
            target.style.display = 'none'
            target.parentElement!.setAttribute('data-fallback', initials)
          }}
        />
      ) : (
        <span>{initials}</span>
      )}
    </div>
  )
}
