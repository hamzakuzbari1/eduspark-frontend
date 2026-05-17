<template>
  <v-app class="eduspark-app">
    <div class="app-ambient" aria-hidden="true">
      <div class="app-ambient__orb app-ambient__orb--1" />
      <div class="app-ambient__orb app-ambient__orb--2" />
      <div class="app-ambient__orb app-ambient__orb--3" />
    </div>
    <div class="page-content">
      <router-view />
    </div>
  </v-app>
</template>

<script setup>
</script>

<style scoped>
.eduspark-app {
  min-height: 100vh;
}
</style>
