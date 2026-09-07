<template>
    <div class="my-list flex flex-col justify-center items-center">
        <ul class="list flex flex-col gap-4">
            <li v-for="doc in folders" :key="doc" >
                <div class="items w-full flex items-center justify-start gap-4">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 0 0-1.883 2.542l.857 6a2.25 2.25 0 0 0 2.227 1.932H19.05a2.25 2.25 0 0 0 2.227-1.932l.857-6a2.25 2.25 0 0 0-1.883-2.542m-16.5 0V6A2.25 2.25 0 0 1 6 3.75h3.879a1.5 1.5 0 0 1 1.06.44l2.122 2.12a1.5 1.5 0 0 0 1.06.44H18A2.25 2.25 0 0 1 20.25 9v.776" />
                    </svg>
                    <h4>C\\Users\\hp\\documents\\note.txt</h4>
                </div>
            </li>
        </ul>
    </div>
</template>

<script lang="ts">

export default {
    props: {

        folders: {
            type: Array,
            default: () => []
        }
        
    }
}

</script>

<style scoped>
.my-list{
    width: 100%;
}

.list{
    background-color: #fff;
    border-radius: 0.5rem;
    padding: 1rem;
}

.items {
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #eaeff4;
}
</style>
