import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import gsap from 'gsap';
import ScrollVelocity from './react-bits/ScrollVelocity.jsx';
import Magnet from './react-bits/Magnet.jsx';
import RotatingText from './react-bits/RotatingText.jsx';
import CircularText from './react-bits/CircularText.jsx';
import './menu-motion.css';

const preference=matchMedia('(prefers-reduced-motion: reduce)');
function useReducedMotion(){
  const [reduced,setReduced]=useState(preference.matches);
  useEffect(()=>{const update=e=>setReduced(e.matches);preference.addEventListener('change',update);return()=>preference.removeEventListener('change',update)},[]);
  return reduced;
}
function Ribbon(){
  const reduced=useReducedMotion();
  return reduced ? <span className="ribbon-static">Massas artesanais · Escolha seu molho · Feito para saborear</span> : <ScrollVelocity texts={['Massas artesanais ✳ Escolha seu molho ✳ Feito para saborear ✳']} velocity={65} className="menu-ribbon-text"/>;
}
function Action(){
  const reduced=useReducedMotion();
  return <Magnet disabled={reduced} padding={25} magnetStrength={5} maxOffset={7}><a className="hero-action" href="#cardapio">Escolher meu prato <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M12 4v16m-6-6 6 6 6-6"/></svg></a></Magnet>;
}
createRoot(document.querySelector('#menuRibbon')).render(<Ribbon/>);
const original=document.querySelector('.hero-action');
const actionRoot=document.createElement('div');
actionRoot.className='hero-action-root';
original.replaceWith(actionRoot);
createRoot(actionRoot).render(<Action/>);
const ornament=document.createElement('div');
ornament.className='hero-ornament';
ornament.setAttribute('aria-hidden','true');
ornament.innerHTML='<svg viewBox="0 0 240 240" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="120" cy="125" r="75" fill="#251a10"/><circle cx="120" cy="125" r="62"/><g class="pasta-swirl"><path d="M88 108c-16 26 20 49 41 33s-2-43-21-29 2 29 15 18-9-19-15-9m-13-23c20-20 55-4 53 25s-39 43-58 20m9 9c25 14 58-9 49-35M91 119c-8 19 14 35 31 29" stroke-width="3"/><path d="M115 92c-2-18 12-22 21-21-1 14-9 23-21 21Z" fill="currentColor" stroke="none"/></g><path d="M24 68v44m10-44v44m10-44v44m-20-15c0 25 20 25 20 0m-10 25v66m177-120c-15 19-18 43-5 47h7m0-47v120"/><g class="food-steam" opacity=".7"><path d="M98 49c-9-14 10-17 2-31m20 27c-9-14 10-17 2-31m20 35c-9-14 10-17 2-31"/></g></svg>';
document.querySelector('.menu-hero').append(ornament);
function LiveHeadline(){
  const reduced=useReducedMotion();
  return <><span className="live-label">Seu próximo prato</span>{<RotatingText texts={['Feito à mão.','Cheio de sabor.','Do seu jeito.']} rotationInterval={2100} staggerDuration={reduced ? 0 : .035} effect={reduced ? 'slide' : 'flip'} initial={reduced ? {opacity:0} : undefined} animate={reduced ? {opacity:1} : undefined} exit={reduced ? {opacity:0} : undefined} transition={reduced ? {duration:.65,ease:'easeInOut'} : undefined} mainClassName="live-words"/>}</>;
}
function Seal(){
  const reduced=useReducedMotion();
  return reduced ? <div className="seal-static">Da Massa ✳ Artesanal</div> : <CircularText text="DA MASSA • MASSAS ARTESANAIS • " size={135} fontSize={12} fontWeight={600} spinDuration={12} color="#e0bf77"><span className="seal-center">DM</span></CircularText>;
}
const headline=document.createElement('div');headline.className='live-headline';document.querySelector('.hero-content').append(headline);createRoot(headline).render(<LiveHeadline/>);
const seal=document.createElement('div');seal.className='hero-seal';document.querySelector('.hero-detail').append(seal);createRoot(seal).render(<Seal/>);
const shapes=document.createElement('div');shapes.className='hero-floating';shapes.setAttribute('aria-hidden','true');shapes.innerHTML='<span><svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 37C4 14 22 5 40 7c2 20-7 37-30 30ZM10 37 33 14m-14 14 0-12m7 5h11"/></svg></span><span><svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2"><path d="m10 6 30 4-2 30-30-4Z" stroke-dasharray="3 2"/><circle cx="24" cy="23" r="9"/></svg></span><span><svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 37C4 14 22 5 40 7c2 20-7 37-30 30ZM10 37 33 14"/></svg></span>' ;document.querySelector('.menu-hero').append(shapes);
// Movimento automático; a preferência de acessibilidade do sistema é preservada.
const media=gsap.matchMedia();
media.add('(prefers-reduced-motion: no-preference)',()=>{
  const cleanup=[];
  gsap.to('.pasta-swirl',{rotation:360,duration:32,repeat:-1,ease:'none',svgOrigin:'120 125'});
  gsap.to('.food-steam',{y:-10,opacity:.2,duration:2.5,repeat:-1,yoyo:true,ease:'sine.inOut'});
  gsap.to('.hero-ornament',{y:-12,duration:3.5,repeat:-1,yoyo:true,ease:'sine.inOut',force3D:true});
  gsap.to('.hero-floating span',{y:-32,rotation:150,duration:3.5,stagger:.6,repeat:-1,yoyo:true,ease:'sine.inOut'});
  document.querySelectorAll('.menu-card').forEach(card=>{
    const image=card.querySelector('.card-photo img');
    if(image)gsap.fromTo(image,{scale:1},{scale:1.055,duration:5,repeat:-1,yoyo:true,ease:'sine.inOut'});
    const enter=()=>{gsap.to(card,{y:-4,duration:.25,ease:'power2.out',overwrite:'auto'})};
    const leave=()=>{gsap.to(card,{y:0,duration:.25,overwrite:'auto'})};
    const pointerEnter=e=>{if(e.pointerType==='mouse')enter()};
    card.addEventListener('pointerenter',pointerEnter);card.addEventListener('pointerleave',leave);
    cleanup.push(()=>{card.removeEventListener('pointerenter',pointerEnter);card.removeEventListener('pointerleave',leave)});
  });
  const categoryObserver=new MutationObserver(records=>{
    for(const record of records){
      if(record.target.classList.contains('active'))gsap.fromTo(record.target.querySelectorAll('.menu-card'),{y:10},{y:0,stagger:.045,duration:.35,ease:'power2.out',overwrite:'auto'});
    }
  });
  document.querySelectorAll('.cat-section').forEach(section=>categoryObserver.observe(section,{attributes:true,attributeFilter:['class']}));
  return()=>{cleanup.forEach(fn=>fn());categoryObserver.disconnect();gsap.killTweensOf('.menu-card, .card-photo img');gsap.set('.menu-card, .card-photo img',{clearProps:'transform'})};
});

// Movimento reduzido troca deslocamentos por transições suaves, sem desligar tudo.
media.add('(prefers-reduced-motion: reduce)',()=>{
  gsap.to('.hero-ornament',{opacity:.75,duration:2.8,repeat:-1,yoyo:true,ease:'sine.inOut'});
  gsap.to('.food-steam',{opacity:.2,duration:2.5,repeat:-1,yoyo:true,ease:'sine.inOut'});
  gsap.to('.ribbon-static, .seal-static',{opacity:.7,duration:2.8,repeat:-1,yoyo:true,ease:'sine.inOut'});
});
