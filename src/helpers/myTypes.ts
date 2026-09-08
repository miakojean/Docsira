export interface File {
    name: string
    extension: string
    path: string
}

export interface Folder {
    name: string
    files: File[]

}