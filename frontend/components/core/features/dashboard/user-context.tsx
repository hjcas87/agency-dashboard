'use client'

import * as React from 'react'

export type UserInfo = {
  id: number
  email: string
  name: string
}

const UserContext = React.createContext<UserInfo | null>(null)

export function UserProvider({ user, children }: { user: UserInfo | null; children: React.ReactNode }) {
  return <UserContext.Provider value={user}>{children}</UserContext.Provider>
}

export function useUser() {
  return React.useContext(UserContext)
}
