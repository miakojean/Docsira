<template>
  <div class="my-file-cards">
    <div class="my-file-header">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
        </svg>

    </div>

    <div class="my-file-body flex flex-col items-center justify-center gap-4">

        <div class="icon-wrapper flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-file-type-pdf">
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                <path d="M5 12v-7a2 2 0 0 1 2 -2h7l5 5v4" />
                <path d="M5 18h1.5a1.5 1.5 0 0 0 0 -3h-1.5v6" />
                <path d="M17 18h2" />
                <path d="M20 15h-3v6" />
                <path d="M11 15v6h1a2 2 0 0 0 2 -2v-2a2 2 0 0 0 -2 -2h-1" />
            </svg>
        </div>

        <span>{{ document.file_name }}</span>

    </div>

    <div class="divider"></div>

    <div class="my-file-footer flex items-center justify-around">
        <div class="size-wrapper flex flex-col justify-items-start">
            <span>Taille</span>
            <span>{{document.size}} Ko</span>
        </div>
        <div class="initials-wrapper">
            <button class="btn-wrapper">A</button>
        </div>
    </div>
  </div>
</template>

<script>
export default {

    props:{
        document:{
            type: Object,
            default:{}
        }
    },
    emits:['open', 'preview', 'detail', 'rename', 'share', 'download', 'delete'],
    setup(props,{emit}){

    }
}
</script>

<style scoped>

.my-file-cards{
    width: 280px;
    height: 300px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #f9f8f8;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 1rem;
}

.my-file-header{
    width: 100%;
    display: flex;
    justify-content: flex-end;
}

.my-file-body span{
    font-size: 0.9rem;
    font-weight: 500;
}

.icon-wrapper{
    height: 90px;
    width: 80px;
    border: 1px solid #ddd;
}

.size-wrapper span{
    font-size: 0.8rem;
    font-weight: 400;
    color: #999999;
}
.my-file-footer{
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem;
}

.btn-wrapper{
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-color-ligth);
    color: #f9f8f8;
    height: 30px;
    width: 30px;
}
</style>