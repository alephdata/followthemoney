import { useRouter } from 'next/router'

function NavLinks({ children, href }: any) {
  const router = useRouter()
  const style = {
    marginRight: 10,
    color: router.asPath === href ? 'red' : 'black',
  }

  const handleClick = (e: any) => {
    e.preventDefault()
    router.push(href)
  }


  return (
    <a href={href} onClick={handleClick} style={style}>
      {children}
    </a>
  )
}

export default NavLinks
