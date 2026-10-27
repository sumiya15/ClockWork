import {useState} from 'react';
const PHOTOS={
 campus:{title:'Campus',alt:'Modern campus building beside a lake',position:'50% 52%'},
 laboratory:{title:'Laboratory',alt:'Microscope, laboratory glassware and safety glasses',position:'50% 50%'},
 classroom:{title:'Classroom',alt:'Empty classroom with rows of desks and chairs',position:'50% 55%'},
 library:{title:'Library',alt:'Library aisle between bookshelves',position:'50% 60%'}
};
export const PHOTO_LABEL='Illustrative photo — not inspection evidence';
export default function CampusImage({compact=false,banner=false,kind='campus'}){
 const [failed,setFailed]=useState(false),photo=PHOTOS[kind]||PHOTOS.campus;
 const source=Object.hasOwn(PHOTOS,kind)?kind:'campus';
 return <figure className={`campus-image ${compact?'campus-thumb':''} ${banner?'campus-banner':''}`}>
 {failed?<div className="campus-fallback" role="img" aria-label={`${photo.title} photo unavailable`}><svg viewBox="0 0 100 60" aria-hidden="true"><path d="M10 22L50 5L90 22M17 22v30h66V22M30 30v13M50 30v22M70 30v13" fill="none" stroke="currentColor" strokeWidth="4"/></svg><span>{photo.title} photo unavailable</span></div>:<img src={`${import.meta.env.BASE_URL}photos/${source}.jpg`} width="800" height="450" alt={`${photo.alt}. ${PHOTO_LABEL}. Not inspection evidence.`} loading={banner?'eager':'lazy'} decoding="async" style={{objectPosition:photo.position}} onError={()=>setFailed(true)}/>}
 {!compact&&<figcaption>{failed?'Illustration fallback — photo unavailable':PHOTO_LABEL}</figcaption>}
 </figure>;
}
export function FacilitiesGallery(){return <section className="demo-card case-section facilities-gallery"><h3>Facilities preview</h3><p className="muted">{PHOTO_LABEL}. Not verified inspection evidence.</p><div className="facility-grid">{['laboratory','classroom','library'].map(kind=><div key={kind}><CampusImage kind={kind} compact/><h4>{PHOTOS[kind].title}</h4></div>)}</div></section>;}
